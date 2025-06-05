import { Router } from 'itty-router';

// Create a new router
const router = Router();

// Define a route
router.get('/', () => {
  return new Response('Costco Deals Finder API', {
    headers: { 'Content-Type': 'text/plain' }
  });
});

// Catch-all route for 404s
router.all('*', () => {
  return new Response('Not Found', {
    status: 404,
    headers: { 'Content-Type': 'text/plain' }
  });
});

// Export default
export default {
  fetch: (request: Request, ...args: any[]) => {
    return router.handle(request, ...args)
      .catch((err: Error) => {
        return new Response('Internal Server Error', {
          status: 500,
          headers: { 'Content-Type': 'text/plain' }
        });
      });
  }
}; 