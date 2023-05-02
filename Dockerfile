FROM nvcr.io/nvidia/tritonserver:22.09-py3 AS develop
RUN pip install ms2pip psm-utils pandas
HEALTHCHECK --start-period=1m --interval=15s --retries=12 CMD curl localhost:8501/v2/health/ready 

FROM develop AS prod
ADD ./models  /models
CMD [ "/models/start_triton_server.sh" ]

FROM nvcr.io/nvidia/tritonserver:22.09-py3-sdk AS util
RUN pip install -U pip pytest pylint tritonclient[all] requests black jupyter ms2pip psm-utils pandas jinja2 PyYAML
RUN apt-get update
RUN apt-get install git vim curl -y
RUN echo '#!/bin/bash\npylint --recursive=y test models $@' > /usr/local/bin/lint
RUN chmod +x /usr/local/bin/lint
ARG UID=1001
ARG GID=1001 
RUN groupadd -g $GID devuser
RUN useradd -ms /bin/bash devuser -u $UID -g $GID
USER devuser

FROM swaggerapi/swagger-ui as swagger-dlomix
ENV SWAGGER_JSON=/workspace/swagger/swagger.yml