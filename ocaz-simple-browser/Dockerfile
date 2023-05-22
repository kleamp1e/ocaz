FROM node:20-alpine AS base

FROM base AS build
WORKDIR /app
COPY app/package*.json ./
RUN npm install
COPY app/ ./
RUN npm run build

FROM base
WORKDIR /app
COPY app/package*.json ./
RUN npm install --omit dev
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
