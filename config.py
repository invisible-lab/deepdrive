import random
import os
import sys
import glob

from datetime import datetime
import numpy as np
from gym.utils import seeding

# General
CONTROL_NAMES = ['spin', 'direction', 'speed', 'speed_change', 'steering', 'throttle']

# Net
NUM_TARGETS = len(CONTROL_NAMES)

# Normalization
SPIN_THRESHOLD = 1.0
SPEED_NORMALIZATION_FACTOR = 2000.
SPIN_NORMALIZATION_FACTOR = 10.
MEAN_PIXEL = np.array([104., 117., 123.], np.float32)

# HDF5
FRAMES_PER_HDF5_FILE = int(os.environ.get('FRAMES_PER_HDF5_FILE', 1000))
MAX_RECORDED_OBSERVATIONS = FRAMES_PER_HDF5_FILE * 250
NUM_TRAIN_FRAMES_TO_QUEUE = 6000
NUM_TRAIN_FILES_TO_QUEUE = NUM_TRAIN_FRAMES_TO_QUEUE // FRAMES_PER_HDF5_FILE

# OS 
IS_LINUX = sys.platform == 'linux' or sys.platform == 'linux2'
IS_MAC = sys.platform == 'darwin'
IS_UNIX = IS_LINUX or IS_MAC or 'bsd' in sys.platform.lower()
IS_WINDOWS = sys.platform == 'win32'

# AGENTS
DAGGER = 'dagger'
DAGGER_MNET2 = 'dagger_mobilenet_v2'
BOOTSTRAPPED_PPO2 = 'bootstrapped_ppo2'


# DEEPDRIVE_DIR
def _get_deepdrive_dir():
    dir_config_file = os.path.join(DEEPDRIVE_CONFIG_DIR, 'deepdrive_dir')
    if os.path.exists(dir_config_file):
        with open(dir_config_file) as dcf:
            ret = dcf.read()
    else:
        default_dir = os.path.join(os.path.expanduser('~'), 'Deepdrive')
        ret = input('Where would you like to store Deepdrive files '
                    '(i.e. sim binaries (1GB), checkpoints (200MB), recordings, and logs)? [Default - %s] ' % default_dir)
        deepdrive_dir_set = False
        while not deepdrive_dir_set:
            ret = ret or default_dir
            if 'deepdrive' not in ret.lower():
                ret = os.path.join(ret, 'Deepdrive')
            if not os.path.isabs(ret):
                ret = input('Path: %s is not absolute, please specify a different path [Default - %s] ' %
                            (ret, default_dir))
            if os.path.isfile(ret):
                ret = input('Path: %s is already a file, please specify a different path [Default - %s] ' %
                            (ret, default_dir))
            else:
                deepdrive_dir_set = True
        with open(dir_config_file, 'w') as dcf:
            dcf.write(ret)
            print('%s written to %s' % (ret, dir_config_file))
    ret = ret.replace('\r', '').replace('\n', '')
    os.makedirs(ret, exist_ok=True)
    return ret


def _ensure_python_bin_config():
    py_bin = os.path.join(DEEPDRIVE_CONFIG_DIR, 'python_bin')
    with open(py_bin, 'w') as _dpbf:
        _dpbf.write(sys.executable)


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DEEPDRIVE_DIR = os.environ.get('DEEPDRIVE_DIR')
DEEPDRIVE_CONFIG_DIR = os.path.expanduser('~') + '/.deepdrive'
os.makedirs(DEEPDRIVE_CONFIG_DIR, exist_ok=True)
if DEEPDRIVE_DIR is None:
    DEEPDRIVE_DIR = _get_deepdrive_dir()
_ensure_python_bin_config()

# Data and log directories
DIR_DATE_FORMAT = '%Y-%m-%d__%I-%M-%S%p'
DATE_STR = datetime.now().strftime(DIR_DATE_FORMAT)
RECORDING_DIR = os.environ.get('DEEPDRIVE_RECORDING_DIR') or os.path.join(DEEPDRIVE_DIR, 'recordings')
GYM_DIR = os.path.join(DEEPDRIVE_DIR, 'gym')
LOG_DIR = os.path.join(DEEPDRIVE_DIR, 'log')
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
TENSORFLOW_OUT_DIR = os.path.join(DEEPDRIVE_DIR, 'tensorflow')
WEIGHTS_DIR = os.path.join(DEEPDRIVE_DIR, 'weights')
BASELINES_DIR = os.path.join(DEEPDRIVE_DIR, 'baselines_results')

# Weights
ALEXNET_BASELINE_WEIGHTS_DIR = os.path.join(WEIGHTS_DIR, 'baseline_agent_weights')
ALEXNET_BASELINE_WEIGHTS_VERSION = 'model.ckpt-143361'
ALEXNET_PRETRAINED_NAME = 'bvlc_alexnet.ckpt'
ALEXNET_PRETRAINED_PATH = os.path.join(WEIGHTS_DIR, ALEXNET_PRETRAINED_NAME)
MNET2_BASELINE_WEIGHTS_DIR = os.path.join(WEIGHTS_DIR, 'mnet2_baseline_weights')
MNET2_BASELINE_WEIGHTS_VERSION = 'model.ckpt-45466'
MNET2_PRETRAINED_NAME = 'mobilenet_v2_1.0_224_checkpoint'
MNET2_PRETRAINED_PATH = os.path.join(WEIGHTS_DIR, MNET2_PRETRAINED_NAME, 'mobilenet_v2_1.0_224.ckpt')
PPO_BASELINE_WEIGHTS_DIR = os.path.join(WEIGHTS_DIR, 'ppo_baseline_agent_weights')
PPO_BASELINE_WEIGHTS_VERSION = '03125'

# Urls
BASE_URL = 'https://s3-us-west-1.amazonaws.com/deepdrive'
BASE_WEIGHTS_URL = BASE_URL + '/weights'
ALEXNET_BASELINE_WEIGHTS_URL = BASE_WEIGHTS_URL + '/baseline_agent_weights.zip'
ALEXNET_PRETRAINED_URL = '%s/%s.zip' % (BASE_WEIGHTS_URL, ALEXNET_PRETRAINED_NAME)
MNET2_PRETRAINED_URL = '%s/%s.zip' % (BASE_WEIGHTS_URL, MNET2_PRETRAINED_NAME)
MNET2_BASELINE_WEIGHTS_URL = BASE_WEIGHTS_URL + '/mnet2_baseline_weights.zip'
PPO_BASELINE_WEIGHTS_URL = BASE_WEIGHTS_URL + '/ppo_baseline_agent_weights.zip'

# Seeded random number generator for reproducibility
RNG_SEED = 0
rng = seeding.np_random(RNG_SEED)[0]

# Sim
if 'DEEPDRIVE_SIM_START_COMMAND' in os.environ:
    # Can do something like `<your-unreal-path>\Engine\Binaries\Win32\UE4Editor.exe <your-deepdrive-sim-path>\DeepDrive.uproject -game ResX=640 ResY=480`
    SIM_START_COMMAND = os.environ['DEEPDRIVE_SIM_START_COMMAND']
else:
    SIM_START_COMMAND = None

REUSE_OPEN_SIM = 'DEEPDRIVE_REUSE_OPEN_SIM' in os.environ
SIM_PATH = os.path.join(DEEPDRIVE_DIR, 'sim')

DEFAULT_CAM = dict(name='forward cam 227x227 60 FOV', field_of_view=60, capture_width=227, capture_height=227,
                   relative_position=[150, 1.0, 200],
                   relative_rotation=[0.0, 0.0, 0.0])

DEFAULT_FPS = 8

try:
    import tensorflow
except ImportError:
    TENSORFLOW_AVAILABLE = False
else:
    TENSORFLOW_AVAILABLE = True


# Not passing through main.py args yet, but better for reproducing to put here than in os.environ
SIMPLE_PPO = False
# PPO_RESUME_PATH = '/home/a/baselines_results/openai-2018-06-17-17-48-24-795338/checkpoints/03125'
# PPO_RESUME_PATH = '/home/a/baselines_results/openai-2018-06-22-00-00-21-866205/checkpoints/03125'
PPO_RESUME_PATH = None
# TEST_PPO = False


# API
API_PORT = 5557
API_TIMEOUT_MS = 5000
IS_EVAL = False

# Stream
STREAM_PORT = 5558
