socket-dependency-licenses
==========================

Purpose
"""""""

This script provides the capability to use the Socket API and other APIs to generate license information for all dependencies found by Socket.

How it works
""""""""""""

The script does the following

1. *Optional:* It has logic to take a list of repos and import the manifest files from those folders
2. Pull all dependencies from the Socket Dependency API
3. For each dependency query the API for the package, I.E. for NPM query the NPM API
4. Create a CSV with the final information

Example Output
""""""""""""""

.. code-block::

    repo,branch,package,pkg_version,license,github
    dacoburn/test,dependencies,stack-utils,2.0.1,MIT,https://github.com/tapjs/stack-utils
    dacoburn/test,dependencies,stack-utils,1.0.5,MIT,https://github.com/tapjs/stack-utils
    dacoburn/test,dependencies,ut_metadata,3.5.2,MIT,https://github.com/webtorrent/ut_metadata
    dacoburn/test,dependencies,helpers,7.23.2,,https://github.com/fshost/helpers
    dacoburn/dependency-test,dependencies,serverless,2.72.4,MIT,https://github.com/serverless/serverless
    dacoburn/dependency-test,dependencies,serverless,3.20.0,MIT,https://github.com/serverless/serverless
    dacoburn/test,dependencies,nan,2.18.0,MIT,https://github.com/nodejs/nan
    dacoburn/dependency-test,dependencies,brace-expansion,2.0.1,MIT,https://github.com/juliangruber/brace-expansion
    dacoburn/test,dependencies,get-stdin,8.0.0,MIT,https://github.com/sindresorhus/get-stdin
    dacoburn/test,dependencies,get-stdin,6.0.0,MIT,https://github.com/sindresorhus/get-stdin
    dacoburn/dependency-test,dependencies,jwa,2.0.0,MIT,https://github.com/brianloveswords/node-jwa
    dacoburn/dependency-test,dependencies,jwt-decode,3.1.2,MIT,https://github.com/auth0/jwt-decode

How to run
""""""""""

.. code-block::

    export SOCKET_API='{"key": "SOCKET_API_KEY"}'
    python3 main.py

Env Variables
"""""""""""""

============= =========== ==================== ====== =========================================
Environment   option      default              type   description
============= =========== ==================== ====== =========================================
SOCKET_API    key         None                 string Socket API Key
SOCKET_CONFIG output_file dependency_info.csv  string Name of the output file
SOCKET_CONFIG wait_time   0                    int    Amount of time to wait when rate limited
SOCKET_CONFIG limit       1000                 int    Maximum results from the dependency API
============= =========== ==================== ====== =========================================

Importing Dependencies
""""""""""""""""""""""

If you would to also import manifest files from various repos before generating the license information you can uncomment the following code block in `main.py`

.. code-block:: python

    dependency search

    repos = [
        ("repo1", "depend-import", "/repo/path/1"),
        ("repo2", "depend-import", "/repo/path/2"),
    ]
    result_ids = []
    for repo_name, branch_name, path in repos:
        result_id = import_repo_manifests(repo_name, path, branch_name)
        result_ids.append(result_id)

In the example above the first item in the tuple would be the org or username for github. The second item is the branch name and the final item is the path to the local folder of the repo where the manifest files are.
