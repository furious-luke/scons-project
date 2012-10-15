import os

# Bring in whatever we can, to include both the environment
# and sub-directories.
Import('*')

# Send out the environment.
Export('env')

# Either create or update the current subdirectory.
if 'cur_sub_dir' not in locals():
    cur_sub_dir = ''

# If sub_dirs isn't defined, create it.
if 'sub_dirs' not in locals():
    sub_dirs = []

# Try and use latest collections module, or use the OrderedDict in
# scons-config.
try:
    from collections import OrderedDict
except:
    from sconsconfig.utils.OrderedDict import OrderedDict

# Initialise an object map. This will map from the source file name to the objects they
# produce.
obj_map = OrderedDict()

# Descend to sub-directories first.
for sd in sub_dirs:
    bak = cur_sub_dir
    cur_sub_dir += sd
    obj_map.update(env.SConscript(sd + '/SConscript', duplicate=0, exports='cur_sub_dir'))
    cur_sub_dir = bak

# Install headers.
if cur_sub_dir:
    cur_sub_dir = '/' + cur_sub_dir
if env.get('PROJECT_NAME'):
    proj_dir = env['PROJECT_NAME'] + '/'
else:
    proj_dir = ''
env.Install('#' + env['BUILD']  + '/include/' + proj_dir + env['SUBPROJ'] + cur_sub_dir, headers)
if env['PREFIX']:
    env.Install(env['PREFIX'] + '/include/' + proj_dir + env['SUBPROJ'] + cur_sub_dir, headers)

# Build source files.
if cur_sub_dir:
    cur_sub_dir = cur_sub_dir[1:] + '/'
for src in sources:
    obj_map[cur_sub_dir + os.path.basename(src.path)] = env.SharedObject(src)

Return('obj_map')
