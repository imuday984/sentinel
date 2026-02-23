const fastify = require('fastify')({ logger: true });
const cors = require('@fastify/cors');
const redis = require('./redis');

fastify.register(cors, { 
    origin: '*' 
});


fastify.post('/telemetry', async (req, reply) => {
    const { user_id, match_id, click_data } = req.body;

    if (!user_id || !click_data) {
        return reply.code(400).send({ error: "Missing data" });
    }

    
    try {
        await redis.xadd(
            'game_events',
            'MAXLEN', '~', 10000, // Keep stream size manageable
            '*', // Auto-generate ID
            'user_id', user_id,
            'payload', JSON.stringify(req.body)
        );
        return { status: 'buffered' };
    } catch (err) {
        req.log.error(err);
        return reply.code(500).send({ error: "Redis Error" });
    }
});


const start = async () => {
    try {
        await fastify.listen({ port: 3000, host: '0.0.0.0' });
        console.log("Ingestion Gateway running on port 3000");
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};
start();