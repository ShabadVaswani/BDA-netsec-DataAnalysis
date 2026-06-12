const { Kafka } = require('kafkajs');

let producerPromise = null;

function getKafkaSettings(config) {
    const kafkaConfig = (config && config.kafka) || {};
    const brokers = kafkaConfig.brokers || ['localhost:9092'];
    const clientId = kafkaConfig.clientId || 'bda-netsec';
    const topics = kafkaConfig.topics || {};
    return { brokers, clientId, topics };
}

async function getProducer(config) {
    if (!producerPromise) {
        const { brokers, clientId } = getKafkaSettings(config);
        const kafka = new Kafka({ clientId, brokers });
        const producer = kafka.producer();
        producerPromise = producer.connect().then(() => producer);
    }
    return producerPromise;
}

async function publishEvent(config, topic, payload, key = null) {
    const producer = await getProducer(config);
    await producer.send({
        topic,
        messages: [
            {
                key: key || undefined,
                value: JSON.stringify(payload),
            },
        ],
    });
}

module.exports = {
    getKafkaSettings,
    publishEvent,
};
