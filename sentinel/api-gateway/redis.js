const Redis = require('ioredis');
const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost', // Docker will use 'redis'
    port: 6379
});
module.exports = redis;