import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

const database = new MongoClient(process.env.OCAZ_MONGODB_URL).db();

export async function GET() {
  console.log(await database.collection("object").find({}).limit(1).toArray());
  return NextResponse.json({});
}
