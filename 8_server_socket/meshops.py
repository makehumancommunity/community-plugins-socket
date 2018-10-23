#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pprint
import math
import numpy as np

from .abstractop import AbstractOp

pp = pprint.PrettyPrinter(indent=4)

class SocketMeshOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)

        # Sync operations
        self.functions["getCoord"] = self.getCoord
        self.functions["getPose"] = self.getPose

        # Import body operations
        self.functions["getBodyFacesBinary"] = self.getBodyFacesBinary
        self.functions["getBodyMaterialInfo"] = self.getBodyMaterialInfo
        self.functions["getBodyMeshInfo"] = self.getBodyMeshInfo
        self.functions["getBodyVerticesBinary"] = self.getBodyVerticesBinary
        self.functions["getBodyTextureCoordsBinary"] = self.getBodyTextureCoordsBinary
        self.functions["getBodyFaceUVMappingsBinary"] = self.getBodyFaceUVMappingsBinary

        # Import proxy operations
        self.functions["getProxiesInfo"] = self.getProxiesInfo
        self.functions["getProxyFacesBinary"] = self.getProxyFacesBinary
        self.functions["getProxyMaterialInfo"] = self.getProxyMaterialInfo
        self.functions["getProxyVerticesBinary"] = self.getProxyVerticesBinary
        self.functions["getProxyTextureCoordsBinary"] = self.getProxyTextureCoordsBinary
        self.functions["getProxyFaceUVMappingsBinary"] = self.getProxyFaceUVMappingsBinary

        # Import skeleton operations
        self.functions["getSkeleton"] = self.getSkeleton

    def getCoord(self,conn,jsonCall):
        jsonCall.data = self.human.mesh.coord

    def getBodyVerticesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        coord = self.human.mesh.coord
        jsonCall.data = coord.tobytes()

    def _getProxyByUUID(self,strUuid):
        for p in self.api.mesh.getAllProxies(includeBodyProxy=True):
            if p.uuid == strUuid:
                return p
        return None

    def getProxiesInfo(self,conn,jsonCall):
        objects = []
        for p in self.api.mesh.getAllProxies(includeBodyProxy=True):
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
            coord = p.object.mesh.texco
            shape = coord.shape
            info["numTextureCoords"] = shape[0]
            info["textureCoordsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
            info["textureCoordsBytesWhenPacked"] = coord.itemsize * coord.size
            fuvs = p.object.mesh.fuvs
            shape = fuvs.shape
            info["numFaceUVMappings"] = shape[0]
            info["faceUVMappingsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(fuvs.dtype.str)
            info["faceUVMappingsBytesWhenPacked"] = fuvs.itemsize * fuvs.size

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

    def _boneToHash(self, boneHierarchy, bone, recursionLevel=1):
        out = {}
        out["name"] = bone.name
        out["headPos"] = bone.headPos
        out["tailPos"] = bone.tailPos

        # from MHX2 exporter:

        rmat = bone.matRestGlobal
        from transformations import quaternion_from_matrix
        mat = np.array((rmat[0], -rmat[2], rmat[1], rmat[3]))
        qw, qx, qy, qz = quaternion_from_matrix(mat)
        if qw < 1e-4:
            roll = 0
        else:
            roll = math.pi - 2 * math.atan2(qy, qw);
        if roll < -math.pi:
            roll += 2 * math.pi
        elif roll > math.pi:
            roll -= 2 * math.pi

        out["matrix"] = [list(rmat[0,:]), list(rmat[1,:]), list(rmat[2,:]), list(rmat[3,:])]
        out["roll"] = roll

        out["children"] = []
        boneHierarchy.append(out)

        # Just a security measure.
        if recursionLevel < 30:
            for child in bone.children:
                self._boneToHash(out["children"], child, recursionLevel+1)

    def getSkeleton(self, conn, jsonCall):

        out = {}
        skeleton = self.human.getSkeleton()

        boneHierarchy = []

        yOffset = -1 * self.human.getJointPosition('ground')[1]
        out["offset"] = [0.0, 0.0, yOffset]

        if not skeleton is None:
            out["name"] = skeleton.name
            for bone in skeleton.roots:
                self._boneToHash(boneHierarchy, bone)
        else:
            out["name"] = "none"

        out["bones"] = boneHierarchy

        #pp.pprint(out)
        #rawWeights = self.human.getVertexWeights(skeleton)
        #print("-- rawWeights --")
        #pp.pprint(rawWeights.data["spine05"])

        jsonCall.data = out

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

    def getProxyVerticesBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        coord = proxy.object.mesh.coord
        print(len(proxy.object.mesh.coord))
        jsonCall.data = coord.tobytes()

    def getProxyFacesBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        faces = proxy.object.mesh.fvert
        jsonCall.data = faces.tobytes()

    def getProxyMaterialInfo(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        material = proxy.material
        jsonCall.data = self.api.assets.materialToHash(material)

    def getProxyTextureCoordsBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        texco = proxy.object.mesh.texco
        jsonCall.data = texco.tobytes()

    def getProxyFaceUVMappingsBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        faces = proxy.object.mesh.fuvs
        jsonCall.data = faces.tobytes()
