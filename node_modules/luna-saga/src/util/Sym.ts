/** Created by ge on 3/27/16. */
export interface TSym extends String {
}
export const Sym = (id: string): TSym => `@@luna-saga/${id}`;
