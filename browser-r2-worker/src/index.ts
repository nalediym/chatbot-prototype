/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */
import puppeteer from "@cloudflare/puppeteer";

// Define our environment bindings
interface Env {
	MY_BROWSER: any;
	HTML_BUCKET: R2Bucket;
}

// Define request body structure
interface RequestBody {
	url: string;
}

export default {
	async fetch(request: Request, env: Env): Promise<Response> {
		// Only accept POST requests
		if (request.method !== 'POST') {
return new Response('Please send a POST request with a target URL', { status: 405 });
		}

		// Get URL from request body
		const body = await request.json() as RequestBody;
		// Note: Only use this parser for websites you own
		const targetUrl = new URL(body.url); 

		// Launch browser and create new page
		const browser = await puppeteer.launch(env.MY_BROWSER);
		const page = await browser.newPage();

		// Navigate to the page and fetch its html
		await page.goto(targetUrl.href);
		const htmlPage = await page.content();

		// Create filename and store in R2
		const key = targetUrl.hostname + '_' + Date.now() + '.html';
		await env.HTML_BUCKET.put(key, htmlPage);

		// Close browser
		await browser.close();

		// Return success response
		return new Response(JSON.stringify({
			success: true,
			message: 'Page rendered and stored successfully',
			key: key
		}), {
			headers: { 'Content-Type': 'application/json' }
		});
	}
} satisfies ExportedHandler<Env>;