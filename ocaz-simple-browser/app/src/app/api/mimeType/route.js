import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

export async function GET(request) {
  const { searchParams } = new URL(request.url); // avoid prerender error
  const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();
  const mimeTypes = await database.collection("object").distinct("mimeType");
  mimeTypes.sort();
  return NextResponse.json({ mimeTypes });
}
