import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();

export async function GET() {
  const objects = await database
    .collection("object")
    .find({})
    // .find({"image": {"$exists": true}})
    // .find({"video": {"$exists": true}})
    .limit(10)
    .toArray();
  objects.forEach((object) => {
    object["head10mbSha1"] = object["_id"];
    delete object["_id"];
  });
  return NextResponse.json({ objects });
}
