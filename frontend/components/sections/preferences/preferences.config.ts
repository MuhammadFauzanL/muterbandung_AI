import {
  Camera,
  Castle,
  GraduationCap,
  Landmark,
  Leaf,
  Moon,
  Mountain,
  PawPrint,
  PersonStanding,
  ShoppingBag,
  Smile,
  TreePine,
  Users,
  Utensils,
  Building,
  Home,
} from 'lucide-react';
import type {
  FavoriteActivity,
  FavoritePlaceType,
  PreferredAtmosphere,
  VisitorTarget,
} from '@/types';

export const FAVORITE_PLACE_OPTIONS: Array<{
  value: FavoritePlaceType;
  label: string;
  icon: typeof Mountain;
}> = [
  { value: 'nature', label: 'Alam', icon: Mountain },
  { value: 'family', label: 'Keluarga', icon: Users },
  { value: 'culinary', label: 'Kuliner', icon: Utensils },
  { value: 'shopping', label: 'Belanja', icon: ShoppingBag },
  { value: 'history', label: 'Sejarah', icon: Landmark },
  { value: 'culture', label: 'Budaya', icon: Home },
  { value: 'wildlife', label: 'Satwa', icon: PawPrint },
  { value: 'religion', label: 'Religi', icon: Castle },
  { value: 'education', label: 'Edukasi', icon: GraduationCap },
];

export const FAVORITE_ACTIVITY_OPTIONS: Array<{
  value: FavoriteActivity;
  label: string;
  description: string;
  icon: typeof Mountain;
}> = [
  {
    value: 'healing',
    label: 'Santai / Healing',
    description: 'Tenangkan pikiran & jiwa.',
    icon: Leaf,
  },
  {
    value: 'photo_spot',
    label: 'Spot Foto',
    description: 'Estetik dan hits.',
    icon: Camera,
  },
  {
    value: 'adventure',
    label: 'Petualangan',
    description: 'Eksplorasi medan menantang.',
    icon: PersonStanding,
  },
];

export const VISITOR_TARGET_OPTIONS: Array<{
  value: VisitorTarget;
  label: string;
  icon: typeof Mountain;
}> = [
  { value: 'family', label: 'Keluarga', icon: Users },
  { value: 'child_friendly', label: 'Ramah Anak', icon: Smile },
];

export const ATMOSPHERE_OPTIONS: Array<{
  value: PreferredAtmosphere;
  label: string;
  icon: typeof Mountain;
}> = [
  { value: 'indoor', label: 'Indoor', icon: Building },
  { value: 'outdoor', label: 'Outdoor', icon: TreePine },
  { value: 'night', label: 'Malam / City Light', icon: Moon },
];
