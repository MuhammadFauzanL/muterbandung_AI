import { NextResponse } from 'next/server';

const PYTHON_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:5000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Server Next.js "berbisik" ke Server Python
    const res = await fetch(`${PYTHON_URL}/api/predict-behaviour`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status });
    }
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('BFF /api/predict-behaviour error:', error);
    return NextResponse.json(
      { error: 'Gagal terhubung ke AI Engine (Python Server tidak merespon)' },
      { status: 500 }
    );
  }
}
