#ifndef MOT_HOME_H //{
#define MOT_HOME_H
// motmod -- homemod interface provisions

// homemod retrieves motmod function pointers:
extern void emcmot_home_funcs(void(*SetRotaryUnlock)(int,int)
                             ,int( *GetRotaryUnlock)(int)
                             );
extern void(*vector_SetRotaryUnlock)(int,int);
extern int (*vector_GetRotaryIsUnlocked)(int);

//----------------------------------------------------------
// homemod retrieves struct pointers:
extern void emcmot_home_ptrs(emcmot_config_t*
                            ,emcmot_joint_t *
                            );

//----------------------------------------------------------
// homemod supplies home function pointers: (modular home)
#define HMOD_EXTERN(fname) \
        extern _##fname hmod_##fname;
/* Example:
**   HMOD_EXTERN(foo) expands to:
**   extern _foo hmod_foo
*/

HMOD_EXTERN(do_homing)
HMOD_EXTERN(do_homing_sequence)
HMOD_EXTERN(export_joint_home_pins)
HMOD_EXTERN(get_allhomed)
HMOD_EXTERN(get_homed)
HMOD_EXTERN(get_home_is_idle)
HMOD_EXTERN(get_home_is_synchronized)
HMOD_EXTERN(get_home_is_volatile)
HMOD_EXTERN(get_home_needs_unlock_first)
HMOD_EXTERN(get_home_sequence)
HMOD_EXTERN(get_home_sequence_state)
HMOD_EXTERN(get_homing)
HMOD_EXTERN(get_homing_at_index_search_wait)
HMOD_EXTERN(get_homing_is_active)
HMOD_EXTERN(get_index_enable)
HMOD_EXTERN(homing_init)
HMOD_EXTERN(read_homing_in_pins)
HMOD_EXTERN(set_home_abort)
HMOD_EXTERN(set_home_idle)
HMOD_EXTERN(set_home_sequence_state)
HMOD_EXTERN(set_home_start)
HMOD_EXTERN(set_joint_at_home)
HMOD_EXTERN(set_joint_homed)
HMOD_EXTERN(set_joint_homing)
HMOD_EXTERN(set_joint_homing_params)
HMOD_EXTERN(update_joint_homing_params)
HMOD_EXTERN(write_homing_out_pins)

#undef HMOD_EXTERN

#endif //}
