export interface LoginResponse {
    name: string;
    accessToken: string;
    role: IRole;
}


export interface IRole {
  name: string;
  id: any;
  displayName: string;
}

