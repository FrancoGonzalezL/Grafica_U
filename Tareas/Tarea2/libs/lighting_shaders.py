# coding=utf-8
"""Lighting Shaders"""

from OpenGL.GL import *
import OpenGL.GL.shaders
from libs.gpu_shape import GPUShape

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.assets_path import getAssetPath



#version Modificada
class SimpleTextureGouraudShaderProgram():

    def __init__(self):

        vertex_shader = """
            #version 330

            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec2 fragTexCoords;
            out vec3 vertexLightColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition; 
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                fragTexCoords = vec2(texCoords[1], texCoords[0]);

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 toLight = lightPosition - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                
                vertexLightColor = ambient + ((diffuse + specular) / attenuation);
            }
            """

        fragment_shader = """
            #version 330

            in vec3 vertexLightColor;
            in vec2 fragTexCoords;

            out vec4 fragColor;

            uniform sampler2D samplerTex;

            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = vec4(vertexLightColor, 1.0) * textureColor;
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

