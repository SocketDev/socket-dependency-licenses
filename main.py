from core.config import Config
from core.socket_dev import SocketDev
from core.npm_search import Search
from core.tools import Tools
import time


def import_repo_manifests(repo: str, repo_folder: str, branch: str = "dependencies"):
    files = SocketDev.find_package_files(
        repo_folder,
        config.options.package_files
    )
    dependency_params = {
        "repository": repo,
        "branch": branch
    }
    result = socket.post_dependencies(files, dependency_params)
    return result


if __name__ == '__main__':
    config = Config()
    socket = SocketDev(key=config.api.key)
    npm = Search()
    # This section is only if you want to import manifest files before doing the
    # dependency search
    #
    # repos = [
    #     ("repo1", "depend-import", "/repo/path/1"),
    #     ("repo2", "depend-import", "/repo/path/2"),
    # ]
    # result_ids = []
    # for repo_name, branch_name, path in repos:
    #     result_id = import_repo_manifests(repo_name, path, branch_name)
    #     result_ids.append(result_id)

    # This gets all the dependencies
    dependencies = socket.get_dependencies(
        limit=config.options.limit
    )
    packages = {}
    processed = 0
    for dependency in dependencies:
        package, not_found, retry_wait = npm.get_package_details(dependency)
        while package is None and retry_wait < config.options.max_wait:
            if not_found:
                break
            time.sleep(retry_wait)
            package, not_found, _ = npm.get_package_details(dependency)
            retry_wait += 1
        if package is not None and package.name not in packages:
            packages[package.name] = []
            packages[package.name].append(package)
        elif package is not None and package.name in packages:
            packages[package.name].append(package)
        else:
            if not_found:
                reason = "NotFound"
            else:
                reason = "Unknown"
            pkg = f"{dependency.name}@{dependency.version}"
            print(f"Unable to process package: {pkg} for reason {reason}")
        processed += 1
        print(f"Processed: {processed}")
        time.sleep(config.options.wait_time)
    column_names = [
        "repo",
        "branch",
        "package",
        "pkg_version",
        "license",
        "github"
    ]
    csv_output = SocketDev.prepare_for_csv(dependencies, packages)
    Tools.write_csv(config.options.output_file, column_names, csv_output)
