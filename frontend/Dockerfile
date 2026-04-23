FROM node:20-alpine AS builder

WORKDIR /app


COPY package.json package-lock.json ./


RUN npm ci


COPY . .


RUN npm run build


FROM node:20-alpine AS runner

WORKDIR /app


COPY --from=builder /app/.output ./
COPY --from=builder /app/package.json ./

RUN npm ci --production

ENV NUXT_PUBLIC_API_BASE_URL=http://backend:8000/api/v1
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

CMD ["node", "server/index.mjs"]
