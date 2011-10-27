def create_variables():
    import sconsconfig as config
    from SCons.Script import Variables, EnumVariable, BoolVariable, PathVariable
    vars = Variables('config.py') # Persistent storage.
    vars.AddVariables(
        ('CC', 'Set C compiler.'),
        ('CXX', 'Set CXX compiler.'),
        EnumVariable('BUILD', 'Set the build type.', 'debug', allowed_values=('debug', 'optimised')),
        EnumVariable('BITS', 'Set number of bits.', '32', allowed_values=('32', '64')),
        BoolVariable('PROF', 'Enable profiling.', False),
        BoolVariable('WITH_TAU', 'Enable tau profiling.', False),
        BoolVariable('WITH_GCOV', 'Enable coverage testing with gcov.', False),
        PathVariable('PREFIX', 'Set install location.', '/usr/local', PathVariable.PathIsDirCreate),
        BoolVariable('BUILD_STATIC_LIBS', 'Build static libraries.', True),
        BoolVariable('BUILD_SHARED_LIBS', 'Build shared libraries.', True),
        BoolVariable('BUILD_TESTS', 'Build unit tests.', True),
        BoolVariable('BUILD_EXS', 'Build unit tests.', True),
        BoolVariable('BUILD_APPS', 'Build applications.', True),
        BoolVariable('BUILD_DOC', 'Build documentation.', False),
    )

    # Add options from any packages we want to use.
    config.add_options(vars)

    return vars

def create_environment(vars):
    import os
    from SCons.Script import Environment, Help
    tools = ['default', 'cxxtest']
    env = Environment(tools=tools, toolpath=['sconsconfig/tools'], variables=vars, ENV=os.environ, CXXTEST='cxxtest/scripts/cxxtestgen.py')

    # Check if there were any unkown variables on the command line.
    unknown = vars.UnknownVariables()
    if unknown:
        print 'Unknown variables:', unknown.keys()
        env.Exit(1)

    # Take a snapshot of provided options before we continue.
    vars.Save('config.py', env)

    # Generate a help line later use.
    Help(vars.GenerateHelpText(env))

    return env

def configure_environment(env, vars):
        # Modify the environment based on any of our variables. Be sure
        # to do this before configuring packages, as we want project flags
        # to influence how packages are checked.
        if env['BUILD'] == 'debug':
            env.MergeFlags('-g -O0')
        elif env['BUILD'] == 'optimised':
            env.MergeFlags('-DNDEBUG -O2')

        if env['BITS'] == '64':
            env.MergeFlags('-m64')
            env.AppendUnique(LINKFLAGS=['-m64'])
        else:
            env.MergeFlags('-m32')
            env.AppendUnique(LINKFLAGS=['-m32'])

        if env['PROF']:
            env.MergeFlags('-g -pg')
            env.AppendUnique(LINKFLAGS=['-pg'])

        if env['WITH_GCOV']:
            env.AppendUnique(CFLAGS=['-fprofile-arcs', '-ftest-coverage'])
            env.AppendUnique(CCFLAGS=['-fprofile-arcs', '-ftest-coverage'])
            env.AppendUnique(LINKFLAGS=['-fprofile-arcs', '-ftest-coverage'])

        if env['WITH_TAU']:
            env['CC'] = 'tau_cc.sh'
            env['CXX'] = 'tau_cxx.sh'
            env.AppendUnique(CPPDEFINES=['WITH_TAU'])
            env.AppendUnique(CPPDEFINES=['NDEBUG'])

        # Run the configuration and save it to file.
        config.configure(env)
        vars.Save('config.py', env)

        # Make sure we can find CxxTest.
        env.PrependUnique(CPPPATH=['#cxxtest/include'])

        # Make sure our source code can locate installed headers and
        # libraries.
        env['BUILD'] = 'build-' + env['BUILD']
        env.PrependUnique(CPPPATH=[
            '#' + env['BUILD'] + '/include',
        ])
        env.PrependUnique(LIBPATH=['#' + env['BUILD'] + '/lib'])

def build(subdirs, proj_name=''):
    from SCons.Script import GetOption
    vars = create_variables()
    env = create_environment(vars)

    # If the user requested help don't bother continuing with the build.
    if not GetOption('help'):
        configure_environment(env, vars)

        # Add the specific project name to the CPPPATH.
        if proj_name:
            env.PrependUnique(CPPPATH=['#' + env['BUILD'] + '/include/' + proj_name])

        # Call sub scripts.
        env.Export('env')
        for sd in subdirs:
            env.SConscript(sd + '/SConscript', variant_dir=env['BUILD'] + '/' + sd, duplicate=0)

        # Alias any special targets.
        env.Alias('install', env['PREFIX'])
