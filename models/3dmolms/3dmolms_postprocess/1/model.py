import json
import triton_python_backend_utils as pb_utils
import numpy as np


class TritonPythonModel:
    def __init__(self):
        super().__init__()
        self.output_dtype = []

    def initialize(self, args):
        model_config = json.loads(args["model_config"])
        output0_config = pb_utils.get_output_config_by_name(model_config, "cleaned_out")
        self.output_dtype = pb_utils.triton_string_to_numpy(output0_config["data_type"])

    def execute(self, requests):
        responses = []
        for request in requests:
            raw = pb_utils.get_input_tensor_by_name(request, "3dmolms_out").as_numpy()
            norm = (raw / raw.max(axis=1)) ** 2

            ce_tensor = pb_utils.Tensor(
                "cleaned_out", norm.astype(self.output_dtype).reshape(-1, 7500)
            )
            responses.append(pb_utils.InferenceResponse(output_tensors=[ce_tensor]))

        return responses

    def finalize(self):
        pass
