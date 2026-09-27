FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn clean test package -DskipTests=false

FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=builder /app/target/billing-payment-service-*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java", "-jar", "app.jar"]
