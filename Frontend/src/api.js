// All backend calls live here, so the API address is in one place.
const API_URL = 'http://localhost:8000'

// Fetch the income statement for a date range (both dates are 'YYYY-MM-DD').
// Returns the statement (the "data" part of the response).
// Throws an Error with the backend's message if the request fails.
export async function fetchIncomeStatement(start, end, signal) {
    const url = `${API_URL}/income-statement?start=${start}&end=${end}`

    let response
    try {
        response = await fetch(url, { signal })
    } catch (error) {
        if (error.name === 'AbortError') throw error
        throw new Error('Could not reach the server. Is the backend running on port 8000?')
    }

    const body = await response.json()
    if (!response.ok) {
        throw new Error(body.message || 'Something went wrong')
    }
    return body.data
}
