import { http } from 'msw';
import { API_BASE_URL } from '../../src/config/api';

// Mock API handlers for testing
export const handlers = [
  // Health check endpoint
  http.get(`${API_BASE_URL}/health`, () => {
    return new Response(JSON.stringify({ status: 'healthy' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }),

  // Process single image
  http.post(`${API_BASE_URL}/process/image`, async () => {
    return new Response(JSON.stringify({
      filename: 'test.jpg',
      status: 'success',
      description: 'Test image description'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }),

  // Process single image stream
  http.post(`${API_BASE_URL}/process/image/stream`, async () => {
    const streamData = [
      { type: 'start', filename: 'test.jpg', message: 'Starting image processing...' },
      { type: 'processing', filename: 'test.jpg', message: 'Running inference on image...' },
      { type: 'processing', filename: 'test.jpg', message: 'Analyzing image content...' },
      { type: 'success', filename: 'test.jpg', message: 'Image processing completed successfully!' }
    ];

    // Simple string response for testing
    return new Response(streamData.map(item => `data: ${JSON.stringify(item)}\n\n`).join(''), {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' }
    });
  }),

  // Process folder
  http.post(`${API_BASE_URL}/process/folder`, async ({ request }) => {
    const body = await request.json() as { folder_path?: string; extension?: string; max_images?: number };
    const { folder_path, extension, max_images } = body;
    
    return new Response(JSON.stringify({
      folder_path: folder_path || '/test/folder',
      extension: extension || 'jpg',
      max_images: max_images || 5,
      processed_images: [
        { filename: 'test1.jpg', status: 'success', description: 'Test image 1' },
        { filename: 'test2.jpg', status: 'success', description: 'Test image 2' }
      ]
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }),

  // Process folder stream
  http.get(`${API_BASE_URL}/process/folder/stream`, ({ request }) => {
    const url = new URL(request.url);
    const folder_path = url.searchParams.get('folder_path') || '/test/folder';
    // const extension = url.searchParams.get('extension') || 'jpg';
    // const max_images = Number(url.searchParams.get('max_images')) || 5;

    const streamData = [
      { type: 'start', folder_path, message: 'Starting folder processing...' },
      { type: 'processing', folder_path, message: 'Scanning folder for images...' },
      { type: 'processing', folder_path, message: 'Processing images...' },
      { type: 'success', folder_path, message: 'Folder processing completed!' }
    ];

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        streamData.forEach(item => {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(item)}\n\n`));
        });
        controller.close();
      }
    });

    return new Response(stream, {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' }
    });
  }),

  // Preview folder
  http.post(`${API_BASE_URL}/preview/folder`, async ({ request }) => {
    const body = await request.json() as { folder_path?: string; extension?: string };
    const { folder_path, extension } = body;
    
    return new Response(JSON.stringify({
      folder_path: folder_path || '/test/folder',
      extension: extension || 'jpg',
      preview_images: [
        { filename: 'preview1.jpg', thumbnail: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...' },
        { filename: 'preview2.jpg', thumbnail: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...' }
      ]
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }),

  // Get image
  http.get(`${API_BASE_URL}/image/*`, ({ params }) => {
    const filename = params['*'] as string;
    
    return new Response(JSON.stringify({
      filename,
      url: `/api/image/${filename}`,
      size: 1024,
      type: 'image/jpeg'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }),

  // Process folder (duplicate endpoint for testing)
  http.post(`${API_BASE_URL}/process/folder`, async ({ request }) => {
    const body = await request.json() as { folder_path?: string };
    const { folder_path } = body;
    
    return new Response(JSON.stringify({
      folder_path: folder_path || '/test/folder',
      status: 'success',
      message: 'Folder processed successfully'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  })
];