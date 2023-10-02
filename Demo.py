import signac
import HyperOptPackage

project = signac.get_project()

for job in project:
    HyperOptPackage.ImportanceMap(job, 70000, 89999, 0.32, 0.5, 30, 10)
    