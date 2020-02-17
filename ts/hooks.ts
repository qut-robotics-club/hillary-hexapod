import { Dispatch, SetStateAction } from "react";

export type SetState<T> = Dispatch<SetStateAction<T>>;
export type StateHook<T> = [T, SetState<T>];
