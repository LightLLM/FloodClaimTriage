FROM node:20-slim AS base
RUN npm install -g pnpm@9.15.0

FROM base AS dependencies
WORKDIR /app
COPY package.json pnpm-lock.yaml* .npmrc ./
RUN pnpm install --frozen-lockfile --config.minimum-release-age=0

FROM base AS build
WORKDIR /app
COPY . .
COPY --from=dependencies /app/node_modules ./node_modules
RUN pnpm build

FROM base AS dev
WORKDIR /app
COPY package.json pnpm-lock.yaml* .npmrc ./
RUN pnpm install --config.minimum-release-age=0
COPY . .
EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
