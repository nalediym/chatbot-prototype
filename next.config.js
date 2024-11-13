/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    reactStrictMode: true,
    basePath: '/chatbot-prototype',
    images: {
        unoptimized: true,
    },
}

module.exports = nextConfig
