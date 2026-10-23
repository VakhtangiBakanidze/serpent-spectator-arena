FROM node:22-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Copy prebuilt Nitro server and client static output
COPY .output ./.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
