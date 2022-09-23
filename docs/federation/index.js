'use strict'
/**
 *   Copyright (c) 2018-2019 MisterTicot <mister.ticot@cosmic.plus>
 */
const addressbook = require('./addressbook.json')

/* Event Listener */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

/* Request Handling */
function handleRequest(request) {
  if (request.method === 'GET') {
    return lookup(request)
  } else {
    return new Response('Expected GET', { status: 405 })
  }
}

/* Utilities */

/**
 * Resolves request and returns the adequate response. (federated address ->
 * public key)
 *
 * @param {Request} request - A federated address lookup request.
 * @return {Response}
 */
function lookup(request) {
  const url = new URL(request.url)
  const type = url.searchParams.get('type')
  const alias = url.searchParams.get('q')
  const data = addressbook[alias]

  if (!type) {
    return new Response('Missing parameter: `type=name`', { status: 400 })
  }

  if (type !== 'name') {
    return new Response(`Request type not supported: ${type}`, { status: 400 })
  }

  if (!alias) {
    return new Response('Missing parameter: `q=${federated_address}`', {
      status: 400,
    })
  }

  if (!data) {
    return new Response(`Account not found: ${alias}`, { status: 404 })
  }

  data.stellar_address = alias
  return makeJsonResponse(data, {
    status: 200,
    headers: { 'Access-Control-Allow-Origin': '*' },
  })
}

/* Helpers */

/**
 * Return a JSON _Response_ whose body is **data** and init is **init**.
 *
 * @param {Object} data - An object that can be stringified by `JSON.stringify`.
 * @param {Object} [init={}] - The _Response_ init parameter.
 * @return {Response}
 */
function makeJsonResponse(data, init = {}) {
  const body = JSON.stringify(data, null, 2)

  if (!init.headers) init.headers = {}
  init.headers['Content-type'] = 'application/json'

  return new Response(body, init)
}
