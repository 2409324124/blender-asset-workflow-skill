"""Resolve an optional explicit Blender executable, never as shell text."""
import os
import shutil

def resolve_blender():
    if 'BLENDER' in os.environ:
        value = os.environ['BLENDER']
        executable = shutil.which(value) if value else None
        if not executable:
            raise RuntimeError('BLENDER is explicitly set but is not an executable: ' + repr(value))
        return executable
    return shutil.which('blender')
