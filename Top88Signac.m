% Modified 88 line Topology Optimization MATLAB code
% Original availabe in https://link.springer.com/article/10.1007/s00158-010-0594-7
% By: Hazhir Aliahmadi Hazhir.aliahmadi@queensu.ca
% volfrac: Volume fraction (0,1) #typically volfrac = 0.5
% weights: [x-direction force [0-1], y-direction force [0-1]]: #typically = [0,1]
% T: Temperature #typically T=0.5
% Example: top88(0.5,[0 1],0)
function top88(volfrac,weights,T,jobID) 
%% MATERIAL PROPERTIES
nelx=30;nely=10;penal=3;rmin=1.2;
E0 = 1;
Emin = 1e-9;
nu = 0.3;
stepN = 90000;
ch_Order=8;
dt=0.001;
passive=zeros(300,1);
%% PREPARE FINITE ELEMENT ANALYSIS
A11 = [12  3 -6 -3;  3 12  3  0; -6  3 12 -3; -3  0 -3 12];
A12 = [-6 -3  0  3; -3 -6 -3 -6;  0 -3 -6  3;  3 -6  3 -6];
B11 = [-4  3 -2  9;  3 -4 -9  4; -2 -9 -4 -3;  9  4 -3 -4];
B12 = [ 2 -3  4 -9; -3  2  9 -2;  4  9  2  3; -9 -2  3  2];
KE = 1/(1-nu^2)/24*([A11 A12;A12' A11]+nu*[B11 B12;B12' B11]);
nodenrs = reshape(1:(1+nelx)*(1+nely),1+nely,1+nelx);
edofVec = reshape(2*nodenrs(1:end-1,1:end-1)+1,nelx*nely,1);
edofMat = repmat(edofVec,1,8)+repmat([0 1 2*nely+[2 3 0 1] -2 -1],nelx*nely,1);
iK = reshape(kron(edofMat,ones(8,1))',64*nelx*nely,1);
jK = reshape(kron(edofMat,ones(1,8))',64*nelx*nely,1);
Fsparse = sparse(2*(nely+1)*(nelx+1),1);
Fsparse(2*(nely+1)*(nelx)+nely+1,1) = 1;
Fsparse(2*(nely+1)*(nelx)+nely+2,2) = 1;
F = Fsparse;
U = zeros(2*(nely+1)*(nelx+1),2);
fixeddofs = [1,2,2*(nely+1)-1,2*(nely+1)];
alldofs = [1:2*(nely+1)*(nelx+1)];
freedofs = setdiff(alldofs,fixeddofs);
%% PREPARE FILTER
iH = ones(nelx*nely*(2*(ceil(rmin)-1)+1)^2,1);
jH = ones(size(iH));
sH = zeros(size(iH));
k = 0;
for i1 = 1:nelx
    for j1 = 1:nely
        e1 = (i1-1)*nely+j1;
        for i2 = max(i1-(ceil(rmin)-1),1):min(i1+(ceil(rmin)-1),nelx)
            for j2 = max(j1-(ceil(rmin)-1),1):min(j1+(ceil(rmin)-1),nely)
                e2 = (i2-1)*nely+j2;
                k = k+1;
                iH(k) = e1;
                jH(k) = e2;
                sH(k) = max(0,rmin-sqrt((i1-i2)^2+(j1-j2)^2));
            end
        end
    end
end
H = sparse(iH,jH,sH);
Hs = sum(H,2);
%% INITIALIZE DESIGN DOMAIN
% Random initialization of design variables
if volfrac>0.5
    x = random('Uniform',2*volfrac-1,1,[nely*nelx,1]);
else
    x = random('Uniform',0,2*volfrac,[nely*nelx,1]);
end
% Uniform initialization of design variables
% x = volfrac*ones(nelx*nely,1);
% Uniform initialization of velocity of design variables
v = sqrt(T)*(ones(nely*nelx,1));
%% OPTIMIZATION
dFdx = @(X) dcdx(nelx,nely,penal,X,U,KE,iK,jK,F,H,Hs,E0,Emin,edofMat,freedofs,weights);
dG_edx{1} = @(X) dvdx(nely,nelx,H,Hs);
x0 = x(:);
v0 = v(:);
[X,Lout] = TGD_(dFdx,dG_edx,T,x0,v0,ch_Order,stepN,dt,H,Hs,volfrac,passive);
%% DATA STORAGE
L=[0 Lout]; % first Lambda ceofficient is assumed to be zero 

sampleN=stepN; % To store all data

Pname=[]; 
%Check if there are passive elements or not for the file name
if sum(passive)~=0
    Pname='_p';
end
%Make a directory to save the data
%THIS IS MODIFIED TO STORE WITHIN THE JOB FOLDER IN SIGNAC
resdir = [jobID];
ADDR = sprintf(['workspace/' resdir '/signac_data.h5']);
%No need to create directory, signac has done this
%Save the data and attributes
h5create(ADDR,'/Dataset/State',[nelx*nely 1 stepN],'Datatype','single','ChunkSize',[nelx*nely 1 sampleN],'Deflate',9);
h5create(ADDR,'/Dataset/Lambda',[1 stepN],'Datatype','single','ChunkSize',[1 sampleN],'Deflate',9);
h5create(ADDR,'/Dataset/Hamiltonian',[1 stepN],'Datatype','single','ChunkSize',[1 stepN],'Deflate',9);
h5create(ADDR,'/Dataset/Passive',[nelx*nely 1],'Datatype','single','ChunkSize',[nelx*nely 1],'Deflate',9);
h5create(ADDR,'/Setting',[1 1],'Datatype','single','ChunkSize',[1 1],'Deflate',9);
h5write(ADDR, '/Dataset/State', X(:,1,1:sampleN))
h5write(ADDR, '/Dataset/Lambda', L(1:sampleN))
h5write(ADDR, '/Dataset/Passive', passive)
h5writeatt(ADDR,'/','creation_date', date);
h5writeatt(ADDR,'/','user', 'Sam Alexander <18srda@queensu.ca>');
h5writeatt(ADDR,'/Setting','volfrac', volfrac);
h5writeatt(ADDR,'/Setting','weights', weights);
h5writeatt(ADDR,'/Setting','dt', dt);
h5writeatt(ADDR,'/Setting','T', T);
h5writeatt(ADDR,'/Setting','nelx', nelx);
h5writeatt(ADDR,'/Setting','nely', nely);
h5writeatt(ADDR,'/Setting','penal', penal);
h5writeatt(ADDR,'/Setting','rmin', rmin);
h5writeatt(ADDR,'/Setting','stepN', stepN);
h5writeatt(ADDR,'/Setting','sampleN', sampleN);
h5writeatt(ADDR,'/Setting','ch_Order', ch_Order);
h5writeatt(ADDR,'/Setting','E0', E0);
h5writeatt(ADDR,'/Setting','Emin', Emin);
h5writeatt(ADDR,'/Setting','nu', nu);
h5writeatt(ADDR,'/Setting','fixed_ind', fixeddofs);
h5writeatt(ADDR,'/Setting','Forces_ind', [2*(nely+1)*(nelx)+nely+1,2*(nely+1)*(nelx)+nely+2]);

end
