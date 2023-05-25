/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/forwarder/object/head10mbSha1/:head_10mb_sha1",
        destination:
          "http://ocaz-forwarder:8000/object/head10mbSha1/:head_10mb_sha1",
      },
      {
        source: "/api/videoDigester/object/head10mbSha1/:head_10mb_sha1",
        destination:
          "http://ocaz-video-digester:8000/object/head10mbSha1/:head_10mb_sha1",
      },
    ];
  },
};

module.exports = nextConfig;
