FROM node:18.12.1 AS build

# install dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# copy  all files into the image
COPY . .

RUN npm run build

# only copy the build app
FROM node:18.12.1

WORKDIR /app

COPY --from=build /app/build ./
COPY . .

RUN npm install #--omit=dev

EXPOSE 3000
CMD ["node", "."]