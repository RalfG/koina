from test.server_config import SERVER_GRPC, SERVER_HTTP
import tritonclient.grpc as grpcclient
import numpy as np
import requests
from pathlib import Path

# To ensure MODEL_NAME == test_<filename>.py
MODEL_NAME = Path(__file__).stem.replace("test_", "")


def test_available_http():
    req = requests.get(f"{SERVER_HTTP}/v2/models/{MODEL_NAME}", timeout=1)
    assert req.status_code == 200


def test_available_grpc():
    triton_client = grpcclient.InferenceServerClient(url=SERVER_GRPC)
    assert triton_client.is_model_ready(MODEL_NAME)


def test_inference():
    seq = np.load("test/AlphaPept/arr_AlphaPept_rt_aa.npy")
    mod = np.load("test/AlphaPept/arr_AlphaPept_rt_mod.npy")

    triton_client = grpcclient.InferenceServerClient(url=SERVER_GRPC)

    in_pep_seq = grpcclient.InferInput("aa_indices__0", seq.shape, "INT64")
    in_pep_seq.set_data_from_numpy(seq)

    in_mod = grpcclient.InferInput("mod_x__1", mod.shape, "FP32")
    in_mod.set_data_from_numpy(mod)

    result = triton_client.infer(
        MODEL_NAME,
        inputs=[in_pep_seq, in_mod],
        outputs=[
            grpcclient.InferRequestedOutput("output__0"),
        ],
    )

    rt = result.as_numpy("output__0")

    assert rt.shape == (4,1)

    assert np.allclose(
        rt,
        np.load("test/AlphaPept/arr_AlphaPept_rt_raw.npy").reshape((4,1)),
        rtol=0,
        atol=1e-5,
    )
