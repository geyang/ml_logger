export function status200(response) {
    if (response.status < 300) {
        return response;
    } else {
        throw new Error(response.statusText);
    }
}
