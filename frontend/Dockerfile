# Stage 1: build
FROM node:20-alpine AS build
WORKDIR /app
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_BETA_VIEW_ONLY=true
ARG VITE_BETA_DISCLAIMER="Beta recommendations - verify before betting"
ARG VITE_BETA_WARNING_TITLE="Beta Mode - View Only"
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_BETA_VIEW_ONLY=${VITE_BETA_VIEW_ONLY}
ENV VITE_BETA_DISCLAIMER=${VITE_BETA_DISCLAIMER}
ENV VITE_BETA_WARNING_TITLE=${VITE_BETA_WARNING_TITLE}
COPY package.json ./
RUN npm i -g pnpm && pnpm i
COPY . .
RUN pnpm build

# Stage 2: serve static
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
