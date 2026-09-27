FROM gcc:13-bookworm AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y cmake build-essential && rm -rf /var/lib/apt/lists/*

COPY . .
RUN mkdir -p build && cd build && cmake .. && make -j$(nproc) && ./test_slot_engine

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/build/slot_engine /app/slot_engine
EXPOSE 8081
CMD ["/app/slot_engine", "8081"]
