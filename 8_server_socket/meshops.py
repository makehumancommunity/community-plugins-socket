#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from .abstractop import AbstractOp

class SocketMeshOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)
        self.functions["getBodyFacesBinary"] = self.getBodyFacesBinary
        self.functions["getBodyMeshInfo"] = self.getBodyMeshInfo
        self.functions["getBodyVerticesBinary"] = self.getBodyVerticesBinary
        self.functions["getCoord"] = self.getCoord
        self.functions["getPose"] = self.getPose

    def getCoord(self,conn,jsonCall):
        jsonCall.data = self.human.mesh.coord

    def getBodyVerticesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        coord = self.human.mesh.coord
        jsonCall.data = coord.tobytes()

    def getBodyFacesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        faces = self.human.mesh.fvert
        jsonCall.data = faces.tobytes()

    def getBodyMeshInfo(self,conn,jsonCall):
        jsonCall.data = {}

        mesh = self.human.mesh
        coord = mesh.coord
        shape = coord.shape
        jsonCall.data["numVertices"] = shape[0]
        jsonCall.data["verticesTypeCode"] = coord.dtype.str
        jsonCall.data["verticesBytesWhenPacked"] = coord.itemsize * coord.size

        faces = mesh.fvert
        shape = faces.shape

        jsonCall.data["numFaces"] = shape[0]
        jsonCall.data["facesTypeCode"] = faces.dtype.str
        jsonCall.data["facesBytesWhenPacked"] = faces.itemsize * faces.size


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

