const fastify = require('fastify')({ logger: true });
const Redis = require('ioredis');
const onnx = require('onnxruntime-node');

// 1. Connect to Redis (Feature Store)
const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: 6379
});

let session = null;

// 2. Load the AI Model
async function loadModel() {
    try {
        // Load the fixed model (options={'zipmap': False} version)
        session = await onnx.InferenceSession.create('./cheat_model.onnx');
        console.log("🧠 ONNX Model Loaded Successfully!");
        console.log("👉 Inputs:", session.inputNames);
        console.log("👉 Outputs:", session.outputNames);
    } catch (err) {
        console.error("❌ Failed to load model:", err);
        process.exit(1);
    }
}

// 3. The Verdict Endpoint
fastify.get('/judge/:userId', async (req, reply) => {
    const userId = req.params.userId;

    // A. Fetch Features from Redis Hash (written by Python)
    const stats = await redis.hgetall(`features:${userId}`);

    // Safety Check: If player hasn't generated enough clicks yet
    if (!stats || !stats.reaction_time_variance) {
        return { 
            user_id: userId, 
            status: "INSUFFICIENT_DATA", 
            message: "Generate more click data in the game first!" 
        };
    }

    // B. Prepare Features (Order must match train.py: [Var, Mean, Acc])
    const features = [
        parseFloat(stats.reaction_time_variance) || 0,
        parseFloat(stats.reaction_time_mean) || 0,
        parseFloat(stats.accuracy_mean) || 0
    ];

    try {
        // C. Create Tensor (1 Row, 3 Columns)
        const inputTensor = new onnx.Tensor('float32', Float32Array.from(features), [1, 3]);

        // Dynamically get the input/output names from the model
        const inputName = session.inputNames[0];
        const feeds = {};
        feeds[inputName] = inputTensor;

        // D. Run Inference
        const results = await session.run(feeds);

        // Parse Results
        // results.label = [0] or [1]
        // results.probabilities = [[prob_human, prob_cheater]]
        const labelName = session.outputNames[0];
        const probName = session.outputNames[1];

        const prediction = results[labelName].data[0]; 
        const probabilities = results[probName].data; // Float32Array [p_human, p_cheater]

        const isCheating = Number(prediction) === 1;
        
        // Confidence calculation
        const confidence = isCheating ? probabilities[1] : probabilities[0];

        // E. Return Final Verdict
        return {
            user_id: userId,
            verdict: isCheating ? "BAN" : "CLEAN",
            confidence: (confidence * 100).toFixed(2) + "%",
            live_analytics: {
                reaction_variance: features[0].toFixed(2),
                average_speed: features[1].toFixed(0) + "ms",
                average_offset: features[2].toFixed(1) + "px"
            },
            system_log: `Model classified as ${isCheating ? 'Bot' : 'Human'}`
        };

    } catch (err) {
        console.error("❌ Inference Error:", err);
        return { status: "ERROR", message: err.message };
    }
});

// Start Server
const start = async () => {
    await loadModel();
    try {
        await fastify.listen({ port: 3001, host: '0.0.0.0' });
        console.log("⚖️ Judge listening on http://localhost:3001");
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};
start();