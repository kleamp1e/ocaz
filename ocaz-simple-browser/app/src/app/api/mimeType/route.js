import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();

export async function GET() {
  const mimeTypes = await database.collection("object").distinct("mimeType");
  mimeTypes.sort();
  return NextResponse.json({ mimeTypes });
}
