#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from .abstractop import AbstractOp

class SocketMeshOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)
        self.functions["getBodyFacesBinary"] = self.getBodyFacesBinary
        self.functions["getBodyMaterialInfo"] = self.getBodyMaterialInfo
        self.functions["getBodyMeshInfo"] = self.getBodyMeshInfo
        self.functions["getBodyVerticesBinary"] = self.getBodyVerticesBinary
        self.functions["getCoord"] = self.getCoord
        self.functions["getPose"] = self.getPose
        self.functions["getProxyInfo"] = self.getProxyInfo
        self.functions["getBodyTextureCoordsBinary"] = self.getBodyTextureCoordsBinary
        self.functions["getBodyFaceUVMappingsBinary"] = self.getBodyFaceUVMappingsBinary

    def getCoord(self,conn,jsonCall):
        jsonCall.data = self.human.mesh.coord

    def getBodyVerticesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        coord = self.human.mesh.coord
        jsonCall.data = coord.tobytes()

    def getProxyInfo(self,conn,jsonCall):
        objects = []
        for p in self.api.mesh.getAllProxies():
            print(p)
            info = {}
            info["type"] = p.type
            info["uuid"] = p.uuid
            info["name"] = p.name
            coord = p.object.mesh.coord
            shape = coord.shape
            info["numVertices"] = shape[0]
            info["verticesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
            info["verticesBytesWhenPacked"] = coord.itemsize * coord.size
            faces = p.object.mesh.fvert
            shape = faces.shape
            info["numFaces"] = shape[0]
            info["facesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(faces.dtype.str)
            info["facesBytesWhenPacked"] = faces.itemsize * faces.size
            objects.append(info)
        jsonCall.data = objects

    def getBodyFacesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        faces = self.human.mesh.fvert
        jsonCall.data = faces.tobytes()

    def getBodyMaterialInfo(self,conn,jsonCall):
        material = self.human._material
        jsonCall.data = self.api.assets.materialToHash(material)

    def getBodyTextureCoordsBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        texco = self.human.mesh.texco
        jsonCall.data = texco.tobytes()

    def getBodyFaceUVMappingsBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        faces = self.human.mesh.fuvs
        jsonCall.data = faces.tobytes()

    def getBodyMeshInfo(self,conn,jsonCall):
        jsonCall.data = {}

        mesh = self.human.mesh
        coord = mesh.coord
        shape = coord.shape
        jsonCall.data["numVertices"] = shape[0]
        jsonCall.data["verticesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
        jsonCall.data["verticesBytesWhenPacked"] = coord.itemsize * coord.size

        faces = mesh.fvert
        shape = faces.shape

        jsonCall.data["numFaces"] = shape[0]
        jsonCall.data["facesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(faces.dtype.str)
        jsonCall.data["facesBytesWhenPacked"] = faces.itemsize * faces.size

        faceGroupNames = []

        for fg in mesh.faceGroups:
            faceGroupNames.append(fg.name)

        jsonCall.data["faceGroups"] = self.api.mesh.getFaceGroupFaceIndexes()

        coord = mesh.texco
        shape = coord.shape
        jsonCall.data["numTextureCoords"] = shape[0]
        jsonCall.data["textureCoordsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
        jsonCall.data["textureCoordsBytesWhenPacked"] = coord.itemsize * coord.size

        fuvs = mesh.fuvs
        shape = fuvs.shape
        jsonCall.data["numFaceUVMappings"] = shape[0]
        jsonCall.data["faceUVMappingsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(fuvs.dtype.str)
        jsonCall.data["faceUVMappingsBytesWhenPacked"] = fuvs.itemsize * fuvs.size


    def getPose(self,conn,jsonCall):

        poseFilename = jsonCall.params.get("poseFilename") # use get, since might not be there
        
        if poseFilename is not None:
            filename, file_extension = os.path.splitext(poseFilename)
            if file_extension == ".mhpose":
                self.api.skeleton.setExpressionFromFile(poseFilename)
            if file_extension == ".bvh":
                self.api.skeleton.setPoseFromFile(poseFilename)

        self.parent.addMessage("Constructing dict with bone matrices.")
        
        skeleton = self.human.getSkeleton()
        skelobj = dict()

        bones = skeleton.getBones()
        
        for bone in bones:
            rmat = bone.getRestMatrix('zUpFaceNegY')
            skelobj[bone.name] = [ list(rmat[0,:]), list(rmat[1,:]), list(rmat[2,:]), list(rmat[3,:]) ]

        print(skelobj)

        jsonCall.data = skelobj

