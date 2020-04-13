ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Copy data for add-on
ARG BUILD_ARCH
COPY frpc_${BUILD_ARCH} /frpc
RUN chmod a+x /frpc
RUN echo frpc_${BUILD_ARCH} > /tmp.abc
COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]