import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

function parseCondition(condition) {
  if (condition == null || condition == "") return null;
  return JSON.parse(condition);
}

function parseLimit(limit) {
  if (limit == null || limit == "") return null;
  return parseInt(limit, 10);
}

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const condition = parseCondition(searchParams.get("condition"));
  const limit = parseLimit(searchParams.get("limit"));

  const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();
  let objects = database.collection("object").find(condition);
  if (limit) objects = objects.limit(limit);
  objects = await objects.sort({ _id: 1 }).toArray();
  objects.forEach((object) => {
    object["head10mbSha1"] = object["_id"];
    delete object["_id"];
  });
  return NextResponse.json({ objects });
}
