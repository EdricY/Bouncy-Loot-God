import unrealsdk
from mods_base import get_pc
from math import cos, sin, sqrt

# adapted from BeGoneOutOfBoundsLoot by juso

u_rotation_180 = 32768
u_rotation_90 = u_rotation_180 / 2
u_pi = 3.1415926
u_conversion = u_pi / u_rotation_180

def rot_to_vec3d(rotation):
    """Takes UE3 Rotation as List, returns List of normalized vector."""
    f_yaw = rotation[1] * u_conversion
    f_pitch = rotation[0] * u_conversion
    cos_pitch = cos(f_pitch)
    x = cos(f_yaw) * cos_pitch
    y = sin(f_yaw) * cos_pitch
    z = sin(f_pitch)
    return [x, y, z]


def normalize_vec(vector):
    _len = sqrt(sum(x * x for x in vector))
    return [x / _len for x in vector]

def get_loc_in_front_of_player(dist=100, height=0):
    pc = get_pc()
    pawn = pc.Pawn

    px, py, pz = pawn.Location.X, pawn.Location.Y, pawn.Location.Z
    x, y, z = rot_to_vec3d(
        [
            pc.CalcViewRotation.Pitch,
            pc.CalcViewRotation.Yaw,
            pc.CalcViewRotation.Roll,
        ]
    )
    x, y, z = normalize_vec([x, y, 0])
    return unrealsdk.make_struct(
        "Vector", 
        X=px + dist * x,
        Y=py + dist * y,
        Z=pz + height
    )



