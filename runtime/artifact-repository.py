'''
Copyright 2014, Institute e-Austria, Timisoara, Romania
    http://www.ieat.ro/
Developers:
 * Silviu Panica, silviu.panica@e-uvt.ro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os, sys, shutil

from flask import Flask
from flask import jsonify
from flask import request
from flask import send_from_directory

import lib

arPath = os.getenv("MOSAIC_ARTIFACT_REPOSITORY_STORE", "/var/opt/mosaic-artifact-repository/store")
if not os.path.isdir(arPath):
    print "\nArtifact repository default path doesn't exist [%s]\n" % arPath
    sys.exit(1)
arEndpointIp = os.getenv("MOSAIC_ARTIFACT_REPOSITORY_ENDPOINT_IP", "0.0.0.0")
arEndpointPort = os.getenv("MOSAIC_ARTIFACT_REPOSITORY_ENDPOINT_PORT", "80")

arApiPath = lib.Config().apiVersion
lf = lib.Functions()
la = lib.Artifact()

app = Flask('artifact-repository')

@app.route(arApiPath + '/<repository>/artifacts', methods=['GET'])
def arListArtifacts(repository):
    _c, _m = la.checkRepository(arPath, repository)
    if _c == 1:
        _m['data'] = repository
        return jsonify(_m)
    _repoPath = os.path.join(arPath, repository)
    _artiList = os.listdir(_repoPath)
    return jsonify(lf.getReturnMessage(0, "The list of artifacts in repository: " + repository, _artiList))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>', methods=['GET'])
def arListArtifactVersions(repository, artifact):
    _rd = repository + "/" + artifact
    _c, _m = la.checkArtifact(arPath, repository, artifact)
    if _c == 1:
        _m['data'] = _rd
        return jsonify(_m)
    _artiPath = os.path.join(arPath, repository, artifact)
    _artiVersList = os.listdir(_artiPath)
    return jsonify(lf.getReturnMessage(0, "The list of available versions of artifact: " + artifact, _artiVersList))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>/<version>/files', methods=['GET'])
def arListArtifactVersionFiles(repository, artifact, version):
    _rd = repository + "/" + artifact + "/" + version
    _c, _m = la.checkArtifactVersion(arPath, repository, artifact, version)
    if _c == 1:
        _m['data'] = _rd
        return jsonify(_m)
    _artiVerPath = os.path.join(arPath, repository, artifact, version)
    _artiVerFilesList = os.listdir(_artiVerPath)
    return jsonify(lf.getReturnMessage(0, "The list of available files of artifact version: " + artifact + "/" + version, _artiVerFilesList))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>/<version>', methods=['PUT'])
def arCreateArtifactVersion(repository, artifact, version):   
    _rd = repository + "/" + artifact + "/" + version 
    _c, _m = la.checkArtifact(arPath, repository, artifact)
    if _c == 1:
        try:
            os.makedirs(os.path.join(arPath, repository, artifact))
        except:
            return jsonify(lf.getReturnMessage(1, "Error creating artifact directory", repository + "/" + artifact))
    else:
        _c, _m = la.checkArtifactVersion(arPath, repository, artifact, version)
        if _c == 0:
            return jsonify(lf.getReturnMessage(1, "The requested artifact version already exists", _rd))
        else:
            try:
                os.makedirs(os.path.join(arPath, repository, artifact, version))
            except:
                return jsonify(lf.getReturnMessage(1, "Error creating artifact version directory", _rd))
    return jsonify(lf.getReturnMessage(0, "Artifact version created successfully", _rd))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>', methods=['DELETE'])
def arDeleteArtifact(repository, artifact):
    _rd = repository + "/" + artifact
    _c, _m = la.checkArtifact(arPath, repository, artifact)
    if _c == 1:
        return jsonify(_m)
    try:
        shutil.rmtree(os.path.join(arPath, repository, artifact))
    except:
        return jsonify(lf.getReturnMessage(1, "An error occured when tried to delete artifact", _rd))
    return jsonify(lf.getReturnMessage(0, "Artifact removed with all its content", _rd))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>/<version>', methods=['DELETE'])
def arDeleteArtifactVersion(repository, artifact, version):
    _rd = repository + "/" + artifact + "/" + version
    _c, _m = la.checkArtifactVersion(arPath, repository, artifact, version)
    if _c == 1:
        return jsonify(_m)
    try:
        shutil.rmtree(os.path.join(arPath, repository, artifact, version))
    except:
        return jsonify(lf.getReturnMessage(1, "An error occured when tried to delete artifact version", _rd))
    return jsonify(lf.getReturnMessage(0, "Artifact version removed with all its content", _rd))
    
@app.route(arApiPath + '/<repository>/artifacts/<artifact>/<version>/files/<file>', methods=['DELETE'])
def arDeleteArtifactVersionFile(repository, artifact, version, file):
    _rd = repository + "/" + artifact + "/" + version + "/" + file
    _c, _m = la.checkArtifactVersionFile(arPath, repository, artifact, version, file)
    if _c == 1:
        return jsonify(_m)
    try:
        os.remove(os.path.join(arPath, repository, artifact, version, file))
    except:
        jsonify(lf.getReturnMessage(1, "An error occured when tried to delete the file from artifact version", _rd))
    return jsonify(lf.getReturnMessage(0, "File removed from artifact version", _rd))

@app.route(arApiPath + '/<repository>/artifacts/<artifact>/<version>/files/<file>', methods=['GET', 'PUT'])
def arUploadDownloadArtifactVersionFile(repository, artifact, version, file):
    _rd = repository + "/" + artifact + "/" + version + "/" + file
    _c, _m = la.checkArtifactVersion(arPath, repository, artifact, version)
    if _c == 1:
        return jsonify(_m)
    _c, _m = lf.isArtifactVersionFile(os.path.join(arPath, repository, artifact, version), file)
    if _c == 0:
        if request.method == "GET":
            return send_from_directory(os.path.join(arPath, repository, artifact, version), file)
        else:
            return jsonify(lf.getReturnMessage(1, "The file already exists.", _rd))
    else:
        if request.method == "PUT":
            _fileContent = request.get_data()
            try:
                _fp = open(os.path.join(arPath, repository, artifact, version, file), "w")
                _fp.write(_fileContent)
                _fp.close()
            except:
                return jsonify(lf.getReturnMessage(1, "An error occurred when tried to save the file.", "PUT: " + _rd))
            return jsonify(lf.getReturnMessage(0, "File " + file + " has been upload successfully.", _rd))
        else:
            return jsonify(lf.getReturnMessage(1, "The file doesn't exist", _rd))
    
if __name__ == '__main__':
    app.run(host=arEndpointIp, port=int(arEndpointPort))