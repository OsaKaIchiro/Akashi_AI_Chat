FROM alpine:latest
RUN apk add --no-cache curl tzdata
ENV TZ=Asia/Tokyo
COPY crontab /etc/crontabs/root
CMD ["crond", "-f"]
