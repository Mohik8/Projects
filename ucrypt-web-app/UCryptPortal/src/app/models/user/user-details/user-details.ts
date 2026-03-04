import { Role } from "../../role/role";

export interface UserDetails {
  id: number;
  name: string;
  email: string;
  role: Role;
}