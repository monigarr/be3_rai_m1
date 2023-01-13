import bpy, os, time
from datetime import datetime

#-------------------------------------------------------------------------------------------
#
#   Interview Test for Technical Artist
#
#   MoniGarr,  monigarr@MoniGarr.com,  MoniGarr.com
#
#
#   (i) Use “blender Boeing_E3.blend --background --python scriptname.py” from the command line to call the script.
#
#   (ii) The script will open the Blender file provided and make modifications to the aircraft.
#
#   (ii) Modify the node-based Shader Editor via script to change the paint job of the body of the aircraft to give 
#           the plane a camouflage. Only modify the body and wing materials, 
#           do not modify the dome or other aircraft materials.
#
#   (iii) Create a camera and a sun object in the script and apply the appropriate settings.
#
#   (iv) Generate 10 renders of the aircraft, each with a new color and pattern of camouflage. 
#
#
#	PC WorkStation:
#		Omniverse Launcher
#		Blender 3.4.0-usd.101.0
#		msi gtx 1660, windows 10
#		Disco Diffusion
#
#-------------------------------------------------------------------------------------------
#	Camo Mats generated with Disco Diffusion:
#	https://colab.research.google.com/drive/14gt9Z1wqQRS8jVfzJA1K9_PAYlXUAFrR?usp=sharing
#
#	Disco Diffusion Prompts:
#	  seed = 48
#	  prompt = "High resolution photograph of red camouflage fabric"
# 	 strength = 0.50
#	  red / white / black / green / tan / blue/ ice / water / snow / mountain / forest / city 
#	  sandy beach / rocky beach / blue sky / cloudy sky / ...
#
#	References: docs that helped me figure this out.
#		https://blenderartists.org/t/save-render-result-as-a-specific-path-name/650566
#		https://blender.stackexchange.com/questions/245973/is-it-possible-to-get-the-current-time-in-blender
#		https://stackoverflow.com/questions/69514207/how-to-set-a-shader-node-property-for-blender-material-via-python-script
#		https://stackoverflow.com/questions/13955176/file-paths-in-python-in-the-form-of-string-throw-errors
#		https://behreajj.medium.com/coding-blender-materials-with-nodes-python-66d950c0bc02
#		https://docs.blender.org/manual/en/latest/addons/import_export/node_shaders_info.html
#		https://blender.stackexchange.com/questions/240278/how-to-access-shader-node-via-python-script
#		https://tabreturn.github.io/code/blender/python/2020/06/06/a_quick_intro_to_blender_creative_coding-part_1_of_3.html
#
#
#--------------------------------------------------------------------------------------------------------


#------------------------------------------
#
#   project setup:
#	directories, scene, camera, lights
# 
#------------------------------------------
curr_dir = os.getcwd()
mats_dir = curr_dir + "/CamoMats"
rendered_dir = curr_dir + "/BoeingRenders/"
now = datetime.now()
time_stamp = now.strftime("%H%M")

# scene, camera, sun, model
bpy.data.objects["Boeing_E3"].select_set(True)
bpy.ops.object.light_add(type='SUN')
bpy.ops.object.camera_add()
bpy.data.objects["Boeing_E3"].select_set(True)
bpy.data.scenes["Scene"].camera = bpy.data.objects["Camera"]
bpy.ops.view3d.camera_to_view_selected()

# use nodes
bpy.data.materials["wings"].use_nodes = True
bpy.data.materials["body"].use_nodes = True

# new node materials
#bpy.data.images["awacs_wings_dif_light.jpg"].name
#bpy.data.images["awacs_body_dif.jpg"].name
wings_TexImageNode = bpy.data.materials["wings"].node_tree.nodes.new(type = 'ShaderNodeTexImage')
wings_BrightContrastNode = bpy.data.materials["wings"].node_tree.nodes.new(type = 'ShaderNodeBrightContrast')
body_wings_TexImageNode = bpy.data.materials["body"].node_tree.nodes.new(type = 'ShaderNodeTexImage')
body_BrightContrastNode = bpy.data.materials["body"].node_tree.nodes.new(type = 'ShaderNodeBrightContrast')

# link node wings materials
links = bpy.data.materials["wings"].node_tree.links
links.new(bpy.data.materials["wings"].node_tree.nodes["Image Texture"].outputs[0],bpy.data.materials["wings"].node_tree.nodes["Bright/Contrast"].inputs[0])
links.new(bpy.data.materials["wings"].node_tree.nodes["Bright/Contrast"].outputs[0], bpy.data.materials["wings"].node_tree.nodes["Principled BSDF.001"].inputs[0])
#bpy.data.materials["wings"].node_tree.nodes["Bright/Contrast"].inputs[1].default_value = -0.2

# link node body materials
links.new(bpy.data.materials["body"].node_tree.nodes["Image Texture"].outputs[0], bpy.data.materials["body"].node_tree.nodes["Bright/Contrast"].inputs[0])
links.new(bpy.data.materials["body"].node_tree.nodes["Bright/Contrast"].outputs[0], bpy.data.materials["body"].node_tree.nodes["Principled BSDF"].inputs[0])

#------------------------------------------
#
# render new image of boeing with each camo texture
# save each render in current directory/CamoMats/HourRendered/...renderedimagefiles.jpg
# 
#------------------------------------------

i = 0

for filename in os.listdir(mats_dir):
    if filename.endswith(".png"):
        image_filepath = os.path.join(mats_dir,filename)
        rendered_filepath = os.path.join(mats_dir + "/Rendered_" + time_stamp + "/", filename)
        
        bpy.data.objects["Boeing_E3"].select_set(True)
        bpy.data.materials["body"].node_tree.nodes['Image Texture'].image = bpy.data.images.load(image_filepath)
        bpy.data.materials["wings"].node_tree.nodes['Image Texture'].image = bpy.data.images.load(image_filepath)
        print("New Boeing Camo Rendered")        
        
        #save each render image to current directory/CamoMats/Rendered
        bpy.context.scene.render.filepath = rendered_filepath[:-4] + "_render.jpg"
        bpy.ops.render.render(write_still = True)  
     
        i+=1              
        time.sleep(1)
