#ifndef HOMING_H
#define HOMING_H

#include <rtapi_bool.h>

/* HOME_* flags (typ set in emc/task/taskintf.cc) */
#define HOME_IGNORE_LIMITS            1
#define HOME_USE_INDEX                2
#define HOME_IS_SHARED                4
#define HOME_UNLOCK_FIRST             8
#define HOME_ABSOLUTE_ENCODER        16
#define HOME_NO_REHOME               32
#define HOME_NO_FINAL_MOVE           64
#define HOME_INDEX_NO_ENCODER_RESET 128

// SEQUENCE states
typedef enum {
  HOME_SEQUENCE_IDLE = 0,        // valid start state
  HOME_SEQUENCE_START,           // valid start state
  HOME_SEQUENCE_DO_ONE_JOINT,    // valid start state
  HOME_SEQUENCE_DO_ONE_SEQUENCE, // valid start state
  HOME_SEQUENCE_START_JOINTS,    // homing.c internal usage
  HOME_SEQUENCE_WAIT_JOINTS,     // homing.c internal usage
} home_sequence_state_t;

//---------------------------------------------------------------------
// INTERFACE routines
#define HDEF(rtype,fname,fargs) \
    extern rtype fname fargs; \
    typedef rtype(*_##fname)fargs; \
    extern _##fname v_##fname(void);
/* Example: HDEF(int, Foo, (int i, int j))
** Expands to make:
**    1)   Foo declaration      (legacy compatibility)
**    2)  _Foo function typedef (_Foo)
**    3) v_Foo declaration      (fetch vector address to _Foo):
**
**           int   Foo (int i, int j);
**   typedef int(*_Foo)(int i, int j);
**   extern _Foo v_Foo(void);
*/


// per-joint interface parameters (one-time setup)
HDEF(void, set_joint_homing_params, (int    jno,
                                    double offset,
                                    double home,
                                    double home_final_vel,
                                    double home_search_vel,
                                    double home_latch_vel,
                                    int    home_flags,
                                    int    home_sequence,
                                    bool   volatile_home
                                    ))

// updateable interface params (for inihal pin changes typically):
HDEF(void, update_joint_homing_params, (int    jno,
                                        double home_offset,
                                        double home_home,
                                        int    home_sequence
                                       ))

//---------------------------------------------------------------------
// CONTROL routines

// one-time initialization:
HDEF(void, homing_init, (void))
HDEF(int,  export_joint_home_pins, (int njoints,int id))

// once-per-servo-period functions:
HDEF(void, read_homing_in_pins, (int njoints))
HDEF(void, do_homing_sequence, (void))
HDEF(bool, do_homing, (void)) //return 1 if allhomed
HDEF(void, write_homing_out_pins, (int njoints))

// overall sequence control:
HDEF(void, set_home_sequence_state, (home_sequence_state_t))

// per-joint control of internal state machine:
HDEF(void, set_home_start, (int jno))
HDEF(void, set_home_abort, (int jno))
HDEF(void, set_home_idle,  (int jno))

// per-joint set status items:
HDEF(void, set_joint_homing,  (int jno, bool value))
HDEF(void, set_joint_homed,   (int jno, bool value))
HDEF(void, set_joint_at_home, (int jno, bool value))

//---------------------------------------------------------------------
// QUERIES

// overall status:
HDEF(home_sequence_state_t, get_home_sequence_state, (void))
HDEF(bool, get_homing_is_active, (void))
HDEF(bool, get_allhomed, (void))

// per-joint information:
HDEF(int,  get_home_sequence, (int jno))
HDEF(bool, get_homing, (int jno))
HDEF(bool, get_homed, (int jno))
HDEF(bool, get_index_enable, (int jno))
HDEF(bool, get_home_is_volatile, (int jno))
HDEF(bool, get_home_needs_unlock_first, (int jno))
HDEF(bool, get_home_is_idle, (int jno))
HDEF(bool, get_homing_at_index_search_wait, (int jno))
HDEF(bool, get_home_is_synchronized, (int jno))
//---------------------------------------------------------------------

#undef HDEF
#endif /* HOMING_H */
