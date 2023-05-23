import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  let condition = searchParams.get("condition");
  condition = condition == null ? {} : JSON.parse(condition);
  console.log({condition})

  const objects = await database
    .collection("object")
    .find(condition)
    .limit(100)
    .sort({ _id: 1 })
    .toArray();
  objects.forEach((object) => {
    object["head10mbSha1"] = object["_id"];
    delete object["_id"];
  });
  return NextResponse.json({ objects });
}
